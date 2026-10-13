import { useState, type SubmitEvent } from "react";
import type { SearchParams } from "./api";

type SearchFormProps = {
    onSearch: (params: SearchParams) => void;
}

function toText(value: string): string | undefined {
    const trimmed = value.trim();
    return trimmed ? trimmed : undefined;
}

function toNumber(value: string): number | undefined {
    const trimmed = value.trim();
    return trimmed ? Number(trimmed) : undefined;
}

export function SearchForm(props: SearchFormProps) {
    const [form, setForm] = useState({
        minPrice: "",
        maxPrice: "",
        minBedrooms: "",
        city: "",
        keyword: "",
        targetBudget: "",
    });

    function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        e.preventDefault();
        const searchParams: SearchParams = {
            minPrice: toNumber(form.minPrice),
            maxPrice: toNumber(form.maxPrice),
            minBedrooms: toNumber(form.minBedrooms),
            city: toText(form.city),
            keyword: toText(form.keyword),
            targetBudget: toNumber(form.targetBudget),
        };
        props.onSearch(searchParams);
    }

    return <form onSubmit={handleSubmit}>
        <label>
            Minimum Price
            <input
                type="number"
                value={form.minPrice}
                onChange={e => setForm({ ...form, minPrice: e.target.value})}
            />
        </label>
        <label>
            Maximum Price
            <input
                type="number"
                value={form.maxPrice}
                onChange={e => setForm({ ...form, maxPrice: e.target.value})}
            />
        </label>
        <label>
            Minimum Bedrooms
            <input
                type="number"
                value={form.minBedrooms}
                onChange={e => setForm({ ...form, minBedrooms: e.target.value})}
            />
        </label>
        <label>
            City
            <input 
                value={form.city}
                onChange={e => setForm({ ...form, city: e.target.value })}
            />
        </label>
        <label>
            Keyword
            <input
                value={form.keyword}
                onChange={e => setForm({ ...form, keyword: e.target.value})}
            />
        </label>
        <label>
            Target Budget
            <input
                type="number"
                value={form.targetBudget}
                onChange={e => setForm({ ...form, targetBudget: e.target.value})}
            />
        </label>
        <button type="submit">Search</button>
    </form>
}
